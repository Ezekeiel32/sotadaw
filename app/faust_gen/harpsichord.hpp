/* ------------------------------------------------------------
name: "harpsichord"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Harpsichord -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Harpsichord_H__
#define  __Harpsichord_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Harpsichord
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

static float Harpsichord_faustpower2_f(float value) {
	return value * value;
}

class Harpsichord : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	float fConst2;
	float fConst3;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	float fConst4;
	int iRec4[2];
	float fConst5;
	float fConst6;
	float fConst7;
	int iRec5[2];
	FAUSTFLOAT fHslider2;
	float fConst8;
	float fRec6[2];
	float fVec2[2];
	float fConst9;
	int IOTA0;
	float fVec3[4096];
	float fConst10;
	float fRec7[2];
	float fRec9[2];
	float fRec11[2];
	float fRec13[2];
	float fRec3[3];
	float fVec4[2];
	float fConst11;
	float fConst12;
	float fConst13;
	float fRec2[2];
	FAUSTFLOAT fHslider3;
	
 public:
	Harpsichord() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Harpsichord -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "harpsichord.dsp");
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
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "harpsichord");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.06f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 3.1415927f / fConst0;
		fConst5 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst6 = 1.0f / fConst5;
		fConst7 = 1.0f / std::max<float>(1.0f, 0.014f * fConst0);
		fConst8 = 1.0f / fConst0;
		fConst9 = 0.25f * fConst0;
		fConst10 = 0.5f * fConst0;
		fConst11 = 1.0f / std::tan(879.64594f / fConst0);
		fConst12 = 1.0f - fConst11;
		fConst13 = 1.0f / (fConst11 + 1.0f);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(2.6f);
		fHslider1 = FAUSTFLOAT(4.4e+02f);
		fHslider2 = FAUSTFLOAT(0.5f);
		fHslider3 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec4[l4] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			iRec5[l5] = 0;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec6[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fVec2[l7] = 0.0f;
		}
		IOTA0 = 0;
		for (int l8 = 0; l8 < 4096; l8 = l8 + 1) {
			fVec3[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec9[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec11[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fRec13[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 3; l13 = l13 + 1) {
			fRec3[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fVec4[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec2[l15] = 0.0f;
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
	
	virtual Harpsichord* clone() {
		return new Harpsichord();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("harpsichord");
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(2.6f), FAUSTFLOAT(0.5f), FAUSTFLOAT(6.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+04f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("pluck", &fHslider2, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = float(fHslider1);
		float fSlow4 = 2.0f * fSlow3;
		float fSlow5 = 4.656613e-10f * float(fHslider2);
		float fSlow6 = std::max<float>(fSlow3, 23.44895f);
		float fSlow7 = std::max<float>(2e+01f, std::fabs(fSlow6));
		float fSlow8 = fConst8 * fSlow7;
		float fSlow9 = fConst9 / fSlow7;
		float fSlow10 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst10 / fSlow6));
		int iSlow11 = int(fSlow10);
		int iSlow12 = iSlow11 + 1;
		float fSlow13 = std::floor(fSlow10);
		float fSlow14 = fSlow10 - fSlow13;
		float fSlow15 = fSlow13 + (1.0f - fSlow10);
		float fSlow16 = std::max<float>(1.1920929e-07f, std::fabs(5.01f * fSlow3));
		float fSlow17 = fConst8 * fSlow16;
		float fSlow18 = 1.0f - fConst0 / fSlow16;
		float fSlow19 = std::max<float>(1.1920929e-07f, std::fabs(3.997f * fSlow3));
		float fSlow20 = fConst8 * fSlow19;
		float fSlow21 = 1.0f - fConst0 / fSlow19;
		float fSlow22 = std::max<float>(1.1920929e-07f, std::fabs(2.003f * fSlow3));
		float fSlow23 = fConst8 * fSlow22;
		float fSlow24 = 1.0f - fConst0 / fSlow22;
		float fSlow25 = std::max<float>(1.1920929e-07f, std::fabs(fSlow3));
		float fSlow26 = fConst8 * fSlow25;
		float fSlow27 = 1.0f - fConst0 / fSlow25;
		float fSlow28 = 0.32f * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec1[1] >= fSlow0);
			float fTemp0 = std::max<float>(0.0f, std::min<float>(fConst3 * fRec1[0], std::max<float>(fSlow2 * (fConst2 - fRec1[0]) + 1.0f, 0.0f)) * (1.0f - fConst1 * float(iRec0[0])));
			float fTemp1 = std::tan(fConst4 * std::min<float>(1.5e+04f, fSlow4 + 6.8e+03f * fTemp0 + 2.6e+03f));
			float fTemp2 = 1.0f / fTemp1;
			float fTemp3 = (fTemp2 + 1.4142135f) / fTemp1 + 1.0f;
			iRec4[0] = (iRec4[1] + (iRec4[1] > 0)) * (fSlow0 <= fVec1[1]) + (fSlow0 > fVec1[1]);
			float fTemp4 = float(iRec4[0]);
			iRec5[0] = 1103515245 * iRec5[1] + 12345;
			float fTemp5 = ((1 - iVec0[1]) ? 0.0f : fSlow8 + fRec6[1]);
			fRec6[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = Harpsichord_faustpower2_f(2.0f * fRec6[0] + -1.0f);
			fVec2[0] = fTemp6;
			float fTemp7 = fSlow9 * float(iVec0[1]) * (fTemp6 - fVec2[1]);
			fVec3[IOTA0 & 4095] = fTemp7;
			float fTemp8 = fSlow17 + fRec7[1] + -1.0f;
			int iTemp9 = fTemp8 < 0.0f;
			float fTemp10 = fSlow17 + fRec7[1];
			fRec7[0] = ((iTemp9) ? fTemp10 : fTemp8);
			float fRec8 = ((iTemp9) ? fTemp10 : fSlow17 + fRec7[1] + fSlow18 * fTemp8);
			float fTemp11 = fSlow20 + fRec9[1] + -1.0f;
			int iTemp12 = fTemp11 < 0.0f;
			float fTemp13 = fSlow20 + fRec9[1];
			fRec9[0] = ((iTemp12) ? fTemp13 : fTemp11);
			float fRec10 = ((iTemp12) ? fTemp13 : fSlow20 + fRec9[1] + fSlow21 * fTemp11);
			float fTemp14 = fSlow23 + fRec11[1] + -1.0f;
			int iTemp15 = fTemp14 < 0.0f;
			float fTemp16 = fSlow23 + fRec11[1];
			fRec11[0] = ((iTemp15) ? fTemp16 : fTemp14);
			float fRec12 = ((iTemp15) ? fTemp16 : fSlow23 + fRec11[1] + fSlow24 * fTemp14);
			float fTemp17 = fSlow26 + fRec13[1] + -1.0f;
			int iTemp18 = fTemp17 < 0.0f;
			float fTemp19 = fSlow26 + fRec13[1];
			fRec13[0] = ((iTemp18) ? fTemp19 : fTemp17);
			float fRec14 = ((iTemp18) ? fTemp19 : fSlow26 + fRec13[1] + fSlow27 * fTemp17);
			fRec3[0] = 0.38f * (2.0f * fRec14 + -1.0f) + 0.3f * (2.0f * fRec12 + -1.0f) + 0.18f * (2.0f * fRec10 + -1.0f) + 0.09f * (2.0f * fRec8 + -1.0f) + 0.08f * (fTemp7 - (fSlow15 * fVec3[(IOTA0 - iSlow11) & 4095] + fSlow14 * fVec3[(IOTA0 - iSlow12) & 4095])) + fSlow5 * float(iRec5[0]) * std::max<float>(0.0f, std::min<float>(fConst6 * fTemp4, fConst7 * (fConst5 - fTemp4) + 1.0f)) - (fRec3[2] * ((fTemp2 + -1.4142135f) / fTemp1 + 1.0f) + 2.0f * fRec3[1] * (1.0f - 1.0f / Harpsichord_faustpower2_f(fTemp1))) / fTemp3;
			float fTemp20 = (fRec3[2] + fRec3[0] + 2.0f * fRec3[1]) / fTemp3;
			fVec4[0] = fTemp20;
			fRec2[0] = -(fConst13 * (fConst12 * fRec2[1] - fConst11 * (fTemp20 - fVec4[1])));
			float fTemp21 = fSlow28 * fRec2[0] * fTemp0;
			output0[i0] = FAUSTFLOAT(fTemp21);
			output1[i0] = FAUSTFLOAT(fTemp21);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			iRec4[1] = iRec4[0];
			iRec5[1] = iRec5[0];
			fRec6[1] = fRec6[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec11[1] = fRec11[0];
			fRec13[1] = fRec13[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fVec4[1] = fVec4[0];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
