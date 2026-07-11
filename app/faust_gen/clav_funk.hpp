/* ------------------------------------------------------------
name: "clav_funk"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn ClavFunk -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __ClavFunk_H__
#define  __ClavFunk_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS ClavFunk
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

static float ClavFunk_faustpower2_f(float value) {
	return value * value;
}

class ClavFunk : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst4;
	float fConst6;
	float fConst8;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec3[2];
	float fConst9;
	float fConst10;
	float fConst11;
	int iRec4[2];
	FAUSTFLOAT fHslider1;
	float fRec2[3];
	float fConst12;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fConst13;
	float fRec5[2];
	float fVec2[2];
	float fConst14;
	int IOTA0;
	float fVec3[4096];
	int iRec6[2];
	float fConst15;
	float fRec7[2];
	FAUSTFLOAT fHslider4;
	FAUSTFLOAT fHslider5;
	float fVec4[2];
	float fConst16;
	float fConst17;
	float fConst18;
	float fRec1[2];
	float fRec0[3];
	
 public:
	ClavFunk() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn ClavFunk -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "clav_funk.dsp");
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
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "clav_funk");
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
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		float fConst2 = std::tan(7853.9814f / fConst0);
		float fConst3 = ClavFunk_faustpower2_f(fConst2);
		fConst4 = 2.0f * (1.0f - 1.0f / fConst3);
		float fConst5 = 1.0f / fConst2;
		fConst6 = (fConst5 + -1.4142135f) / fConst2 + 1.0f;
		float fConst7 = (fConst5 + 1.4142135f) / fConst2 + 1.0f;
		fConst8 = 1.0f / fConst7;
		fConst9 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst10 = 1.0f / fConst9;
		fConst11 = 1.0f / std::max<float>(1.0f, 0.012f * fConst0);
		fConst12 = 1.0f / (fConst3 * fConst7);
		fConst13 = 1.0f / fConst0;
		fConst14 = 0.25f * fConst0;
		fConst15 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst16 = 1.0f / std::tan(376.99112f / fConst0);
		fConst17 = 1.0f - fConst16;
		fConst18 = 1.0f / (fConst16 + 1.0f);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(6.5e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.5f);
		fHslider2 = FAUSTFLOAT(0.28f);
		fHslider3 = FAUSTFLOAT(2.2e+02f);
		fHslider4 = FAUSTFLOAT(0.35f);
		fHslider5 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec3[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec4[l3] = 0;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec5[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fVec2[l6] = 0.0f;
		}
		IOTA0 = 0;
		for (int l7 = 0; l7 < 4096; l7 = l7 + 1) {
			fVec3[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			iRec6[l8] = 0;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fVec4[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec1[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 3; l12 = l12 + 1) {
			fRec0[l12] = 0.0f;
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
	
	virtual ClavFunk* clone() {
		return new ClavFunk();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("clav_funk");
		ui_interface->addHorizontalSlider("decay", &fHslider4, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.1f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("duty", &fHslider2, FAUSTFLOAT(0.28f), FAUSTFLOAT(0.1f), FAUSTFLOAT(0.45f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("snap", &fHslider1, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.5f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tone", &fHslider0, FAUSTFLOAT(6.5e+03f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1e+01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / ClavFunk_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -0.90909094f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 0.90909094f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fButton0);
		float fSlow7 = 4.656613e-10f * float(fHslider1);
		float fSlow8 = float(fHslider2);
		float fSlow9 = std::max<float>(float(fHslider3), 23.44895f);
		float fSlow10 = std::max<float>(2e+01f, std::fabs(fSlow9));
		float fSlow11 = fConst13 * fSlow10;
		float fSlow12 = fConst14 / fSlow10;
		float fSlow13 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst0 * (fSlow8 / fSlow9)));
		int iSlow14 = int(fSlow13);
		int iSlow15 = iSlow14 + 1;
		float fSlow16 = std::floor(fSlow13);
		float fSlow17 = fSlow13 - fSlow16;
		float fSlow18 = fSlow16 + (1.0f - fSlow13);
		int iSlow19 = fSlow6 == 0.0f;
		float fSlow20 = 0.88f / std::max<float>(1.0f, fConst0 * float(fHslider4));
		float fSlow21 = float(fHslider5);
		float fSlow22 = 0.421f / fSlow4;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow6;
			iRec3[0] = (iRec3[1] + (iRec3[1] > 0)) * (fSlow6 <= fVec1[1]) + (fSlow6 > fVec1[1]);
			float fTemp0 = float(iRec3[0]);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			fRec2[0] = fSlow7 * float(iRec4[0]) * std::max<float>(0.0f, std::min<float>(fConst10 * fTemp0, fConst11 * (fConst9 - fTemp0) + 1.0f)) - fConst8 * (fConst6 * fRec2[2] + fConst4 * fRec2[1]);
			float fTemp1 = ((1 - iVec0[1]) ? 0.0f : fSlow11 + fRec5[1]);
			fRec5[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = ClavFunk_faustpower2_f(2.0f * fRec5[0] + -1.0f);
			fVec2[0] = fTemp2;
			float fTemp3 = fSlow12 * float(iVec0[1]) * (fTemp2 - fVec2[1]);
			fVec3[IOTA0 & 4095] = fTemp3;
			iRec6[0] = iSlow19 * (iRec6[1] + 1);
			fRec7[0] = fSlow6 + fRec7[1] * float(fVec1[1] >= fSlow6);
			float fTemp4 = fSlow21 * std::max<float>(0.0f, std::min<float>(fConst10 * fRec7[0], std::max<float>(fSlow20 * (fConst9 - fRec7[0]) + 1.0f, 0.12f)) * (1.0f - fConst15 * float(iRec6[0]))) * (fTemp3 - (fSlow18 * fVec3[(IOTA0 - iSlow14) & 4095] + fSlow17 * fVec3[(IOTA0 - iSlow15) & 4095]) - fSlow8 + fConst12 * (fRec2[2] + (fRec2[0] - 2.0f * fRec2[1])));
			fVec4[0] = fTemp4;
			fRec1[0] = -(fConst18 * (fConst17 * fRec1[1] - fConst16 * (fTemp4 - fVec4[1])));
			fRec0[0] = fRec1[0] - fSlow5 * (fSlow3 * fRec0[2] + fSlow1 * fRec0[1]);
			float fTemp5 = fSlow22 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp5);
			output1[i0] = FAUSTFLOAT(fTemp5);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec3[1] = iRec3[0];
			iRec4[1] = iRec4[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			fRec5[1] = fRec5[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			iRec6[1] = iRec6[0];
			fRec7[1] = fRec7[0];
			fVec4[1] = fVec4[0];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
