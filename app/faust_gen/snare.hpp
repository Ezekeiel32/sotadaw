/* ------------------------------------------------------------
name: "snare"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Snare -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Snare_H__
#define  __Snare_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Snare
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float Snare_faustpower2_f(float value) {
	return value * value;
}

class Snare : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fConst3;
	float fConst5;
	float fConst7;
	float fConst8;
	float fConst11;
	float fConst13;
	float fConst15;
	int iRec3[2];
	float fRec2[3];
	float fConst16;
	float fRec1[3];
	FAUSTFLOAT fHslider1;
	float fConst17;
	FAUSTFLOAT fHslider2;
	float fConst18;
	float fRec5[2];
	float fVec2[2];
	float fConst19;
	int IOTA0;
	float fVec3[1024];
	float fConst20;
	float fRec4[2];
	float fRec7[2];
	float fVec4[2];
	float fVec5[2048];
	float fRec6[2];
	FAUSTFLOAT fHslider3;
	float fConst21;
	FAUSTFLOAT fHslider4;
	
 public:
	Snare() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Snare -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "snare.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/pole:author", "Julius O. Smith III");
		m->declare("filters.lib/pole:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/pole:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "snare");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 0.16f * fConst0;
		float fConst4 = std::tan(21991.148f / fConst0);
		fConst5 = 2.0f * (1.0f - 1.0f / Snare_faustpower2_f(fConst4));
		float fConst6 = 1.0f / fConst4;
		fConst7 = (fConst6 + -1.4142135f) / fConst4 + 1.0f;
		fConst8 = 1.0f / ((fConst6 + 1.4142135f) / fConst4 + 1.0f);
		float fConst9 = std::tan(4712.389f / fConst0);
		float fConst10 = Snare_faustpower2_f(fConst9);
		fConst11 = 2.0f * (1.0f - 1.0f / fConst10);
		float fConst12 = 1.0f / fConst9;
		fConst13 = (fConst12 + -1.4142135f) / fConst9 + 1.0f;
		float fConst14 = (fConst12 + 1.4142135f) / fConst9 + 1.0f;
		fConst15 = 1.0f / fConst14;
		fConst16 = 1.0f / (fConst10 * fConst14);
		fConst17 = 0.12f * fConst0;
		fConst18 = 1.0f / fConst0;
		fConst19 = 0.25f * fConst0;
		fConst20 = 0.5f * fConst0;
		fConst21 = 0.5f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(1.0f);
		fHslider1 = FAUSTFLOAT(0.8f);
		fHslider2 = FAUSTFLOAT(1.0f);
		fHslider3 = FAUSTFLOAT(0.5f);
		fHslider4 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec3[l3] = 0;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec1[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec5[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec2[l7] = 0.0f;
		}
		IOTA0 = 0;
		for (int l8 = 0; l8 < 1024; l8 = l8 + 1) {
			fVec3[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec4[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec7[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fVec4[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2048; l12 = l12 + 1) {
			fVec5[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec6[l13] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Snare* clone() {
		return new Snare();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("snare");
		ui_interface->addHorizontalSlider("body", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.3f), FAUSTFLOAT(3.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("snap", &fHslider1, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tone", &fHslider2, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.5f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = float(fHslider0);
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst3 * fSlow1);
		float fSlow3 = fConst8 * float(fHslider1);
		float fSlow4 = 1.0f / std::max<float>(1.0f, fConst17 * fSlow1);
		float fSlow5 = float(fHslider2);
		float fSlow6 = std::max<float>(3.3e+02f * fSlow5, 23.44895f);
		float fSlow7 = std::max<float>(2e+01f, std::fabs(fSlow6));
		float fSlow8 = fConst18 * fSlow7;
		float fSlow9 = fConst19 / fSlow7;
		float fSlow10 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst20 / fSlow6));
		int iSlow11 = int(fSlow10);
		int iSlow12 = iSlow11 + 1;
		float fSlow13 = std::floor(fSlow10);
		float fSlow14 = fSlow10 - fSlow13;
		float fSlow15 = fSlow13 + (1.0f - fSlow10);
		float fSlow16 = std::max<float>(1.8e+02f * fSlow5, 23.44895f);
		float fSlow17 = std::max<float>(2e+01f, std::fabs(fSlow16));
		float fSlow18 = fConst18 * fSlow17;
		float fSlow19 = fConst19 / fSlow17;
		float fSlow20 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst20 / fSlow16));
		int iSlow21 = int(fSlow20);
		int iSlow22 = iSlow21 + 1;
		float fSlow23 = std::floor(fSlow20);
		float fSlow24 = fSlow20 - fSlow23;
		float fSlow25 = fSlow23 + (1.0f - fSlow20);
		float fSlow26 = fConst21 * fSlow5 * float(fHslider3);
		float fSlow27 = float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iVec1[0] = 1;
			iRec0[0] = (iRec0[1] + (iRec0[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec0[0]);
			float fTemp1 = fConst2 * fTemp0;
			float fTemp2 = fConst1 - fTemp0;
			iRec3[0] = 1103515245 * iRec3[1] + 12345;
			fRec2[0] = 4.656613e-10f * float(iRec3[0]) - fConst15 * (fConst13 * fRec2[2] + fConst11 * fRec2[1]);
			fRec1[0] = fConst16 * (fRec2[2] + (fRec2[0] - 2.0f * fRec2[1])) - fConst8 * (fConst7 * fRec1[2] + fConst5 * fRec1[1]);
			int iTemp3 = 1 - iVec1[1];
			float fTemp4 = ((iTemp3) ? 0.0f : fSlow8 + fRec5[1]);
			fRec5[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = Snare_faustpower2_f(2.0f * fRec5[0] + -1.0f);
			fVec2[0] = fTemp5;
			float fTemp6 = float(iVec1[1]);
			float fTemp7 = fSlow9 * fTemp6 * (fTemp5 - fVec2[1]);
			fVec3[IOTA0 & 1023] = fTemp7;
			fRec4[0] = 0.999f * fRec4[1] + fTemp7 - (fSlow15 * fVec3[(IOTA0 - iSlow11) & 1023] + fSlow14 * fVec3[(IOTA0 - iSlow12) & 1023]);
			float fTemp8 = ((iTemp3) ? 0.0f : fSlow18 + fRec7[1]);
			fRec7[0] = fTemp8 - std::floor(fTemp8);
			float fTemp9 = Snare_faustpower2_f(2.0f * fRec7[0] + -1.0f);
			fVec4[0] = fTemp9;
			float fTemp10 = fSlow19 * fTemp6 * (fTemp9 - fVec4[1]);
			fVec5[IOTA0 & 2047] = fTemp10;
			fRec6[0] = 0.999f * fRec6[1] + fTemp10 - (fSlow25 * fVec5[(IOTA0 - iSlow21) & 2047] + fSlow24 * fVec5[(IOTA0 - iSlow22) & 2047]);
			float fTemp11 = fSlow27 * (fSlow26 * (7.2e+02f * fRec6[0] + 1.32e+03f * fRec4[0]) * std::max<float>(0.0f, std::min<float>(fTemp1, fSlow4 * fTemp2 + 1.0f)) + fSlow3 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1]) * std::max<float>(0.0f, std::min<float>(fTemp1, fSlow2 * fTemp2 + 1.0f)));
			output0[i0] = FAUSTFLOAT(fTemp11);
			output1[i0] = FAUSTFLOAT(fTemp11);
			fVec0[1] = fVec0[0];
			iVec1[1] = iVec1[0];
			iRec0[1] = iRec0[0];
			iRec3[1] = iRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec5[1] = fRec5[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			fRec4[1] = fRec4[0];
			fRec7[1] = fRec7[0];
			fVec4[1] = fVec4[0];
			fRec6[1] = fRec6[0];
		}
	}

};

#endif
