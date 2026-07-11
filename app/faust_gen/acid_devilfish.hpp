/* ------------------------------------------------------------
name: "acid_devilfish"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn AcidDevilfish -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __AcidDevilfish_H__
#define  __AcidDevilfish_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS AcidDevilfish
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

class AcidDevilfishSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec16[2];
	
  public:
	
	int getNumInputsAcidDevilfishSIG0() {
		return 0;
	}
	int getNumOutputsAcidDevilfishSIG0() {
		return 1;
	}
	
	void instanceInitAcidDevilfishSIG0(int sample_rate) {
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			iVec2[l12] = 0;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			iRec16[l13] = 0;
		}
	}
	
	void fillAcidDevilfishSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec16[0] = (iVec2[1] + iRec16[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec16[0]));
			iVec2[1] = iVec2[0];
			iRec16[1] = iRec16[0];
		}
	}

};

static AcidDevilfishSIG0* newAcidDevilfishSIG0() { return (AcidDevilfishSIG0*)new AcidDevilfishSIG0(); }
static void deleteAcidDevilfishSIG0(AcidDevilfishSIG0* dsp) { delete dsp; }

static float AcidDevilfish_faustpower2_f(float value) {
	return value * value;
}
static float AcidDevilfish_faustpower4_f(float value) {
	return value * value * value * value;
}
static float AcidDevilfish_faustpower3_f(float value) {
	return value * value * value;
}
static float ftbl0AcidDevilfishSIG0[65536];

class AcidDevilfish : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	float fConst8;
	float fConst9;
	FAUSTFLOAT fHslider0;
	float fRec1[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst10;
	float fRec3[2];
	float fConst11;
	float fConst12;
	float fConst13;
	float fConst14;
	float fConst15;
	float fConst16;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fRec9[2];
	FAUSTFLOAT fHslider4;
	float fRec10[2];
	float fConst17;
	float fConst18;
	FAUSTFLOAT fHslider5;
	float fRec11[2];
	float fConst20;
	float fConst21;
	float fRec13[2];
	float fRec14[2];
	int iRec15[2];
	float fRec12[2];
	float fConst22;
	float fRec17[2];
	FAUSTFLOAT fHslider6;
	float fConst23;
	float fRec18[2];
	float fVec3[2];
	int IOTA0;
	float fVec4[4096];
	float fConst24;
	FAUSTFLOAT fHslider7;
	float fRec19[2];
	float fConst25;
	FAUSTFLOAT fHslider8;
	float fRec22[2];
	float fRec20[2];
	float fRec23[2];
	float fRec4[2];
	float fRec5[2];
	float fRec6[2];
	float fRec7[2];
	float fRec0[3];
	float fConst26;
	
 public:
	AcidDevilfish() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn AcidDevilfish -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("description", "Devil-Fish-grade acid voice: drifting detuned saw pair + sub square into a diode-ladder with velocity-accented squelch and tanh drive");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "acid_devilfish.dsp");
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
		m->declare("filters.lib/nlf2:author", "Julius O. Smith III");
		m->declare("filters.lib/nlf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/nlf2:license", "MIT-style STK-4.3 license");
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
		m->declare("misceffects.lib/cubicnl:author", "Julius O. Smith III");
		m->declare("misceffects.lib/cubicnl:license", "STK-4.3");
		m->declare("misceffects.lib/name", "Misc Effects Library");
		m->declare("misceffects.lib/version", "2.4.0");
		m->declare("name", "acid_devilfish");
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
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
		m->declare("vaeffects.lib/diodeLadder:author", "Eric Tarr");
		m->declare("vaeffects.lib/diodeLadder:license", "MIT-style STK-4.3 license");
		m->declare("vaeffects.lib/name", "Faust Virtual Analog Filter Effect Library");
		m->declare("vaeffects.lib/version", "1.2.1");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		AcidDevilfishSIG0* sig0 = newAcidDevilfishSIG0();
		sig0->instanceInitAcidDevilfishSIG0(sample_rate);
		sig0->fillAcidDevilfishSIG0(65536, ftbl0AcidDevilfishSIG0);
		deleteAcidDevilfishSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(251.32741f / fConst0);
		float fConst2 = AcidDevilfish_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = 44.1f / fConst0;
		fConst9 = 1.0f - fConst8;
		fConst10 = 1.0f / std::max<float>(1.0f, 0.09f * fConst0);
		fConst11 = std::max<float>(1.0f, 0.0012f * fConst0);
		fConst12 = 1.0f / fConst11;
		fConst13 = 0.55f / std::max<float>(1.0f, 0.18f * fConst0);
		fConst14 = 1.0f / std::max<float>(1.0f, 0.07f * fConst0);
		fConst15 = std::max<float>(1.0f, 0.0008f * fConst0);
		fConst16 = 1.0f / fConst15;
		fConst17 = 2.0f / fConst0;
		fConst18 = 6.2831855f / fConst0;
		float fConst19 = 19.477875f / fConst0;
		fConst20 = std::cos(fConst19);
		fConst21 = std::sin(fConst19);
		fConst22 = 0.11f / fConst0;
		fConst23 = 1.0f / fConst0;
		fConst24 = 0.5f * fConst0;
		fConst25 = 0.1f * fConst0;
		fConst26 = 1.0f / (fConst2 * fConst6);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(1.7f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.6f);
		fHslider2 = FAUSTFLOAT(0.17f);
		fHslider3 = FAUSTFLOAT(0.62f);
		fHslider4 = FAUSTFLOAT(1.25e+03f);
		fHslider5 = FAUSTFLOAT(0.78f);
		fHslider6 = FAUSTFLOAT(1.1e+02f);
		fHslider7 = FAUSTFLOAT(0.38f);
		fHslider8 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fVec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec2[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec9[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec10[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec11[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec13[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec14[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			iRec15[l10] = 0;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec12[l11] = 0.0f;
		}
		for (int l14 = 0; l14 < 2; l14 = l14 + 1) {
			fRec17[l14] = 0.0f;
		}
		for (int l15 = 0; l15 < 2; l15 = l15 + 1) {
			fRec18[l15] = 0.0f;
		}
		for (int l16 = 0; l16 < 2; l16 = l16 + 1) {
			fVec3[l16] = 0.0f;
		}
		IOTA0 = 0;
		for (int l17 = 0; l17 < 4096; l17 = l17 + 1) {
			fVec4[l17] = 0.0f;
		}
		for (int l18 = 0; l18 < 2; l18 = l18 + 1) {
			fRec19[l18] = 0.0f;
		}
		for (int l19 = 0; l19 < 2; l19 = l19 + 1) {
			fRec22[l19] = 0.0f;
		}
		for (int l20 = 0; l20 < 2; l20 = l20 + 1) {
			fRec20[l20] = 0.0f;
		}
		for (int l21 = 0; l21 < 2; l21 = l21 + 1) {
			fRec23[l21] = 0.0f;
		}
		for (int l22 = 0; l22 < 2; l22 = l22 + 1) {
			fRec4[l22] = 0.0f;
		}
		for (int l23 = 0; l23 < 2; l23 = l23 + 1) {
			fRec5[l23] = 0.0f;
		}
		for (int l24 = 0; l24 < 2; l24 = l24 + 1) {
			fRec6[l24] = 0.0f;
		}
		for (int l25 = 0; l25 < 2; l25 = l25 + 1) {
			fRec7[l25] = 0.0f;
		}
		for (int l26 = 0; l26 < 3; l26 = l26 + 1) {
			fRec0[l26] = 0.0f;
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
	
	virtual AcidDevilfish* clone() {
		return new AcidDevilfish();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("acid_devilfish");
		ui_interface->addHorizontalSlider("cutoff", &fHslider4, FAUSTFLOAT(1.25e+03f), FAUSTFLOAT(1.2e+02f), FAUSTFLOAT(9e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("detune", &fHslider8, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("drive", &fHslider0, FAUSTFLOAT(1.7f), FAUSTFLOAT(0.4f), FAUSTFLOAT(6.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("envmod", &fHslider3, FAUSTFLOAT(0.62f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("fdecay", &fHslider2, FAUSTFLOAT(0.17f), FAUSTFLOAT(0.03f), FAUSTFLOAT(1.2f), FAUSTFLOAT(0.005f));
		ui_interface->addHorizontalSlider("freq", &fHslider6, FAUSTFLOAT(1.1e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider1, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("reso", &fHslider5, FAUSTFLOAT(0.78f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("sub", &fHslider7, FAUSTFLOAT(0.38f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst8 * float(fHslider0);
		float fSlow1 = float(fButton0);
		int iSlow2 = fSlow1 == 0.0f;
		float fSlow3 = float(fHslider1);
		float fSlow4 = std::max<float>(0.0f, fSlow3 + -0.72f);
		float fSlow5 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2) * (1.24999f * fSlow4 + 1.0f));
		float fSlow6 = fConst8 * float(fHslider3);
		float fSlow7 = 6.07138f * fSlow4 + 2.1f;
		float fSlow8 = fConst8 * float(fHslider4);
		float fSlow9 = 0.45f * fSlow3 + 0.55f;
		float fSlow10 = fConst8 * float(fHslider5);
		float fSlow11 = 14.2856f * fSlow4 + 9.5f;
		float fSlow12 = float(fHslider6);
		float fSlow13 = 0.5f * fSlow12;
		float fSlow14 = fConst8 * float(fHslider7);
		float fSlow15 = fConst8 * float(fHslider8);
		float fSlow16 = 1e+02f * (1.7857f * fSlow4 + 0.55f);
		float fSlow17 = 0.5f * (0.78f * fSlow3 + 0.22f);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fRec1[0] = fSlow0 + fConst9 * fRec1[1];
			fVec1[0] = fSlow1;
			iRec2[0] = iSlow2 * (iRec2[1] + 1);
			float fTemp0 = float(iRec2[0]);
			fRec3[0] = fSlow1 + fRec3[1] * float(fVec1[1] >= fSlow1);
			fRec9[0] = fSlow6 + fConst9 * fRec9[1];
			fRec10[0] = fSlow8 + fConst9 * fRec10[1];
			float fTemp1 = std::min<float>(0.45f, fConst17 * std::max<float>(9e+01f, std::min<float>(fSlow9 * fRec10[0] * std::pow(2.0f, fSlow7 * fRec9[0] * std::max<float>(0.0f, std::min<float>(fConst16 * fRec3[0], std::max<float>(fSlow5 * (fConst15 - fRec3[0]) + 1.0f, 0.0f)) * (1.0f - fConst14 * fTemp0))), 1.15e+04f)));
			float fTemp2 = std::tan(fConst18 * std::pow(1e+01f, 3.0f * fTemp1 + 1.0f));
			float fTemp3 = fTemp2 + 1.0f;
			float fTemp4 = fTemp2 * (1.0f - 0.25f * (fTemp2 / fTemp3)) + 1.0f;
			float fTemp5 = 0.5f * (fRec4[1] * fTemp2 / fTemp3) + fRec5[1];
			float fTemp6 = fTemp2 * fTemp5 / fTemp4;
			float fTemp7 = 0.5f * fTemp6;
			float fTemp8 = fTemp3 * fTemp4;
			float fTemp9 = AcidDevilfish_faustpower2_f(fTemp2);
			float fTemp10 = fTemp2 * (1.0f - 0.25f * (fTemp2 / fTemp4)) + 1.0f;
			float fTemp11 = fTemp7 + fRec6[1];
			float fTemp12 = fTemp2 * fTemp11 / fTemp10;
			float fTemp13 = fTemp4 * fTemp10;
			float fTemp14 = fTemp2 * (1.0f - 0.5f * (fTemp2 / fTemp10)) + 1.0f;
			float fTemp15 = fTemp12 + fRec7[1];
			fRec11[0] = fSlow10 + fConst9 * fRec11[1];
			float fTemp16 = fSlow11 * fRec11[0] + 0.012893219f;
			float fTemp17 = 17.0f - 9.7f * std::pow(fTemp1, 1e+01f);
			fRec13[0] = fConst21 * fRec14[1] + fConst20 * fRec13[1];
			int iTemp18 = 1 - iVec0[1];
			fRec14[0] = float(iTemp18) + fConst20 * fRec14[1] - fConst21 * fRec13[1];
			int iTemp19 = (fRec13[1] <= 0.0f) & (fRec13[0] > 0.0f);
			iRec15[0] = 1103515245 * iRec15[1] + 12345;
			fRec12[0] = fRec12[1] * float(1 - iTemp19) + 4.656613e-10f * float(iRec15[0]) * float(iTemp19);
			float fTemp20 = ((iTemp18) ? 0.0f : fConst22 + fRec17[1]);
			fRec17[0] = fTemp20 - std::floor(fTemp20);
			float fTemp21 = 0.0016f * ftbl0AcidDevilfishSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec17[0]), 65535))] + 0.0011f * fRec12[0] + 1.0f;
			float fTemp22 = std::max<float>(fSlow13 * fTemp21, 23.44895f);
			float fTemp23 = std::max<float>(2e+01f, std::fabs(fTemp22));
			float fTemp24 = ((iTemp18) ? 0.0f : fRec18[1] + fConst23 * fTemp23);
			fRec18[0] = fTemp24 - std::floor(fTemp24);
			float fTemp25 = AcidDevilfish_faustpower2_f(2.0f * fRec18[0] + -1.0f);
			fVec3[0] = fTemp25;
			float fTemp26 = float(iVec0[1]) * (fTemp25 - fVec3[1]) / fTemp23;
			fVec4[IOTA0 & 4095] = fTemp26;
			float fTemp27 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst24 / fTemp22));
			int iTemp28 = int(fTemp27);
			float fTemp29 = std::floor(fTemp27);
			fRec19[0] = fSlow14 + fConst9 * fRec19[1];
			fRec22[0] = fSlow15 + fConst9 * fRec22[1];
			float fTemp30 = std::max<float>(1.1920929e-07f, std::fabs(fSlow12 * fTemp21 * (0.0052f * fRec22[0] + 1.0f) + 0.11f));
			float fTemp31 = fRec20[1] + fConst23 * fTemp30;
			float fTemp32 = fTemp31 + -1.0f;
			int iTemp33 = fTemp32 < 0.0f;
			fRec20[0] = ((iTemp33) ? fTemp31 : fTemp32);
			float fRec21 = ((iTemp33) ? fTemp31 : fTemp31 + fTemp32 * (1.0f - fConst0 / fTemp30));
			float fTemp34 = std::max<float>(1.1920929e-07f, std::fabs(fSlow12 * fTemp21));
			float fTemp35 = fRec23[1] + fConst23 * fTemp34;
			float fTemp36 = fTemp35 + -1.0f;
			int iTemp37 = fTemp36 < 0.0f;
			fRec23[0] = ((iTemp37) ? fTemp35 : fTemp36);
			float fRec24 = ((iTemp37) ? fTemp35 : fTemp35 + fTemp36 * (1.0f - fConst0 / fTemp34));
			float fTemp38 = std::max<float>(-1.0f, std::min<float>(1.0f, fSlow16 * (0.5f * (2.0f * fRec24 + -1.0f) + 0.34f * (2.0f * fRec21 + -1.0f) + fConst25 * fRec19[0] * (fTemp26 - fVec4[(IOTA0 - iTemp28) & 4095] * (fTemp29 + (1.0f - fTemp27)) - (fTemp27 - fTemp29) * fVec4[(IOTA0 - (iTemp28 + 1)) & 4095]))));
			float fTemp39 = fTemp2 * ((1.5f * fTemp38 * (1.0f - 0.33333334f * AcidDevilfish_faustpower2_f(fTemp38)) - fTemp17 * fTemp16 * (0.0411643f * fRec4[1] + 0.02058215f * fTemp6 + 0.02058215f * fTemp12 + 0.0051455377f * (AcidDevilfish_faustpower3_f(fTemp2) * fTemp15 / (fTemp13 * fTemp14))) / fTemp3) * (0.5f * (fTemp9 / (fTemp10 * fTemp14)) + 1.0f) / (0.0051455377f * (AcidDevilfish_faustpower4_f(fTemp2) * fTemp17 * fTemp16 / (fTemp8 * fTemp10 * fTemp14)) + 1.0f) + (fTemp11 + 0.5f * (fTemp2 * fTemp15 / fTemp14)) / fTemp10 - fRec7[1]) / fTemp3;
			float fTemp40 = fTemp2 * (0.5f * ((fRec7[1] + fTemp39) * (0.25f * (fTemp9 / fTemp13) + 1.0f) + (fTemp5 + 0.5f * fTemp12) / fTemp4) - fRec6[1]) / fTemp3;
			float fTemp41 = fTemp2 * (0.5f * ((fRec6[1] + fTemp40) * (0.25f * (fTemp9 / fTemp8) + 1.0f) + (fRec4[1] + fTemp7) / fTemp3) - fRec5[1]) / fTemp3;
			float fTemp42 = fTemp2 * (0.5f * (fRec5[1] + fTemp41) - fRec4[1]) / fTemp3;
			fRec4[0] = fRec4[1] + 2.0f * fTemp42;
			fRec5[0] = fRec5[1] + 2.0f * fTemp41;
			fRec6[0] = fRec6[1] + 2.0f * fTemp40;
			fRec7[0] = fRec7[1] + 2.0f * fTemp39;
			float fRec8 = fRec4[1] + fTemp42;
			fRec0[0] = fSlow17 * (tanhf(fRec8 * fRec1[0]) * std::max<float>(0.0f, std::min<float>(fConst12 * fRec3[0], std::max<float>(fConst13 * (fConst11 - fRec3[0]) + 1.0f, 0.45f)) * (1.0f - fConst10 * fTemp0)) / std::sqrt(std::max<float>(0.4f, fRec1[0]))) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			float fTemp43 = fConst26 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp43);
			output1[i0] = FAUSTFLOAT(fTemp43);
			iVec0[1] = iVec0[0];
			fRec1[1] = fRec1[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec3[1] = fRec3[0];
			fRec9[1] = fRec9[0];
			fRec10[1] = fRec10[0];
			fRec11[1] = fRec11[0];
			fRec13[1] = fRec13[0];
			fRec14[1] = fRec14[0];
			iRec15[1] = iRec15[0];
			fRec12[1] = fRec12[0];
			fRec17[1] = fRec17[0];
			fRec18[1] = fRec18[0];
			fVec3[1] = fVec3[0];
			IOTA0 = IOTA0 + 1;
			fRec19[1] = fRec19[0];
			fRec22[1] = fRec22[0];
			fRec20[1] = fRec20[0];
			fRec23[1] = fRec23[0];
			fRec4[1] = fRec4[0];
			fRec5[1] = fRec5[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
